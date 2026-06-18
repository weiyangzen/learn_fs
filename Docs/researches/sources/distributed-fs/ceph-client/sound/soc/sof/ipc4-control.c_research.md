# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-control.c

## Purpose
IPC4 ALSA kcontrol implementation for SOF. It translates mixer, switch, enum, bytes, and extended bytes control operations into IPC4 module large-config set/get messages, keeps the kernel-side control cache coherent with firmware, and handles firmware-originated ALSA control update notifications.

## APIs, Types, and Functions
The exported integration object is `tplg_ipc4_control_ops`. Key helpers are `sof_ipc4_set_get_kcontrol_data()`, `sof_ipc4_set_volume_data()`, `sof_ipc4_set_generic_control_data()`, `sof_ipc4_set_get_bytes_data()`, bytes TLV handlers `sof_ipc4_bytes_ext_put()` and `_sof_ipc4_bytes_ext_get()`, `sof_ipc4_control_update()`, `sof_ipc4_widget_kcontrol_setup()`, and `sof_ipc4_set_up_volume_table()`. The code consumes `struct sof_ipc4_control_data`, `struct sof_ipc4_control_msg_payload`, `struct sof_ipc4_gain_params`, and `struct sof_abi_hdr` definitions from `ipc4-topology.h`.

## Control Flow, State, and Persistence
Runtime `put` callbacks update `scontrol->ipc_control_data` first, then send IPC only when the component is runtime-active. The common IPC helper locates the owning widget by `comp_id`, locks or asserts the widget setup mutex, patches the module instance id into the message template, and skips firmware access when the widget is not set up. Volume controls send either one all-channel gain payload or one payload per channel. Switch and enum controls use generic `{id,num_elems,chanv}` payloads. Bytes controls either use generic raw parameter payloads or the IPC4 bytes-control wrapper with ABI header, size checks, and dirty-cache refresh. Extended bytes put keeps `old_ipc_control_data` as a rollback copy and restores it if firmware rejects the new payload. Firmware notifications search the active widget and control by module id, instance id, parameter id, and control index, update cached values or mark the control dirty, then call `snd_ctl_notify_one()`.

## Dependencies and Integration
Depends on SOF component/control lists, runtime PM state, widget setup mutexes, IPC ops `set_get_data()`, topology-provided control metadata, ALSA TLV/user-copy APIs, and the IPC4 module notification format. `ipc4-topology.c` initializes the control data and embeds module ids once widget module information is known.

## Risks and Test Signals
Risks include stale cached values when firmware changes a control but the follow-up refresh fails, user TLV size or ABI-header mistakes, rollback relying on a valid previous bytes payload, skipped firmware writes while suspended, and duplicated widget lookup logic by `comp_id`. Test signals are mixer/switch/enum read-write round trips, extended bytes invalid magic/oversize tests, runtime-suspended put/get behavior, firmware notification delivery to user space, widget setup pushing defaults, and failure injection for rejected bytes payload rollback.
