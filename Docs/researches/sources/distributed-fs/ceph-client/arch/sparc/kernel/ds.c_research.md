# sources/distributed-fs/ceph-client/arch/sparc/kernel/ds.c

## Purpose
`ds.c` implements the Sun Logical Domains domain-services VIO driver. It negotiates the domain-services protocol over an LDC stream, registers service capabilities, dispatches service data to handlers, and exposes LDOM control helpers for reboot, poweroff, variable updates, machine-description updates, and CPU dynamic reconfiguration.

## Important APIs, Types, and Functions
The protocol is modeled by `ds_msg_tag`, version/register/unregister/data/nack packet structs, and `ds_cap_state`. `ds_info` owns one LDC channel, receive buffer, handshake state, capability table copy, and list linkage. Exported or externally meaningful functions are `ldom_set_var()`, `ldom_reboot()`, and `ldom_power_off()`. Service handlers include `md_update_data()`, `domain_shutdown_data()`, `domain_panic_data()`, optional `dr_cpu_data()`, `ds_pri_data()`, and `ds_var_data()`. Driver entry points are `ds_probe()` and `ds_init()`.

## Control Flow and State
`ds_probe()` allocates per-channel state, copies `ds_states_template`, creates an LDC channel, binds it, and links `ds_info_list` under `ds_lock`. `ds_event()` reacts to LDC up/reset/data events. On up, `ds_up()` sends `DS_INIT_REQ`; `ds_handshake()` expects `DS_INIT_ACK`, then `register_services()` sends `DS_REG_REQ` for each capability. Registration ACK/NACK updates each `ds_cap_state.state`. `DS_DATA` packets are copied into `ds_work_list` and processed by `ds_thread()`, so service-specific work runs outside the LDC receive loop.

## Persistence and Dependencies
Persistent kernel state includes `ds_info_list`, per-capability handles/states, `ds_var_doorbell` and `ds_var_response`, `full_boot_str`, and `reboot_data_supported`. The file depends on LDC/VIO, hypervisor calls, machine-description code, CPU hotplug, reboot/poweroff APIs, and the local `kernel.h` helper `kimage_addr_to_ra()` on sparc64.

## Integration Points, Risks, and Test Signals
Integration points include the VIO bus match type `domain-services-port`, LDC transport, `mdesc_update()`, `add_cpu()`/`remove_cpu()`, `fixup_irqs()`, and hypervisor reboot-data APIs. Risks center on packet length trust, deadlocks around global `ds_lock`, timeout-only `ldom_set_var()` completion, missing driver remove path, and the assumption that handles encode capability index in the top 32 bits. Test signals are successful service registration messages, variable set responses, LDOM shutdown/panic requests, machine-description update handling, CPU hotplug DR requests, and reboot command behavior on systems with and without `HV_GRP_REBOOT_DATA`.
