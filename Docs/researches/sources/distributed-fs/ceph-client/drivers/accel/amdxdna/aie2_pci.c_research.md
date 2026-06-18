# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_pci.c

Purpose: implements the AIE2-family AMD XDNA PCI hardware operations exposed through `struct amdxdna_dev_ops`. It owns firmware loading/startup, PSP/SMU/mailbox bring-up, runtime configuration, PM handoff, hardware suspend/resume, and user-visible query/state ioctls for AIE metadata, telemetry, power, preemption, resources, and context status.

Important APIs, types, and functions: `aie2_ops` wires this file into the generic driver. `aie2_init()` maps PCI BARs, loads `npu.sbin` or `npu_7.sbin`, allocates MSI-X vectors, creates PSP state, starts hardware, initializes the XRS solver, and starts runtime PM. `aie2_hw_start()` creates the mailbox, starts SMU and PSP, reads management-channel SRAM descriptors, starts the management channel, initializes firmware/runtime PM, queries firmware/AIE metadata, and allocates async error handling. `aie2_get_info()`, `aie2_get_array()`, and `aie2_set_state()` dispatch DRM query/set requests under runtime PM. XRS callbacks `aie2_xrs_load()` and `aie2_xrs_unload()` create and destroy firmware contexts for allocated columns.

Control flow: probe calls `aie2_init()` under `dev_lock`; open clients later use ops callbacks for context creation and command submission. Resume restarts hardware then resumes every client hardware context; suspend walks clients to suspend contexts before stopping firmware and hardware. Most user queries enter `drm_dev_enter()`, resume runtime PM, copy data to/from user buffers, and suspend runtime PM.

State and persistence: persistent runtime state is in `struct amdxdna_dev_hdl`: mapped BAR bases, management mailbox resources, firmware protocol/version/features, AIE metadata, power levels, current TOPS, preemption flags, context count, and last async error. Nothing is stored on disk; firmware choice is from kernel firmware files.

Dependencies and integration points: depends on PCI, firmware loader, PSP and SMU helpers, `aie2_message.c` firmware mailbox commands, `amdxdna_mailbox`, `amdxdna_pm`, `aie2_solver`, and UAPI structs from `drm/amdxdna_accel.h`.

Risks: startup and unwind ordering is critical; failure paths must stop PSP/SMU/mailbox in reverse order. User-buffer size checks gate telemetry/status copies. Protocol feature-mask checks drive preemption and command-mode behavior. Hypervisor rejection, firmware absence, or bad SRAM management-channel descriptors block probe.

Test signals: bind supported PCI IDs, firmware load success/failure, suspend/resume with active contexts, runtime PM autosuspend, every `GET_INFO`/`GET_ARRAY`/`SET_STATE` parameter, bad user buffers, unsupported firmware protocol, and XRS allocation/release under concurrent contexts.
