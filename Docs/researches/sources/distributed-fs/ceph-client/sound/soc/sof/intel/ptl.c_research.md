<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.c

## Purpose
Panther Lake/Wildcat Lake SOF HDA hardware descriptor and ops customization layer. It builds on Lunar Lake and Meteor Lake code while adding Panther Lake IPC4 microphone privacy handling through the SoundWire multi-link shim.

## Important APIs, Types, and Functions
`sof_ptl_set_ops()` calls `sof_lnl_set_ops()` and then installs `sof_ptl_set_mic_privacy()` into `struct sof_ipc4_fw_data`. Mic privacy helpers include `sof_ptl_check_mic_privacy_irq()`, `sof_ptl_process_mic_privacy()`, `sof_ptl_mic_privacy_work()`, and `sof_ptl_set_mic_privacy()`. Exported descriptors are `ptl_chip_info` and `wcl_chip_info`, both `sof_intel_dsp_desc` instances for ACE 3.0-class platforms.

## Control Flow, State, and Persistence
During ops initialization, the base LNL ops are installed and the IPC4 private data gains a callback for firmware-provided mic privacy capabilities. When capability data indicates DDZE is enabled and not forced, the driver programs the SoundWire mic privacy mask and initializes delayed work in `sof_intel_hda_dev`. IRQ checks and processing only accept alternate SoundWire link events (`AZX_REG_ML_LEPTR_ID_SDW`); the worker reads current privacy state and sends `sof_ipc4_mic_privacy_state_change()` to firmware. Runtime state is transient in `hdev->mic_privacy` and HDA bus registers.

## Dependencies and Integration
Depends on HDA register and multi-link APIs, IPC4 Intel mic privacy types, MTL/LNL HDA helpers, SoundWire wake/IRQ helpers, and HDA mlink namespace exports. `ptl_chip_info` and `wcl_chip_info` integrate with PCI platform descriptor files outside this item and reuse MTL/LNL IPC registers, ROM status, D0i3 offset, CL boot, power-down, and interrupt-disable callbacks.

## Risks and Test Signals
Risks include misinterpreting firmware capability bits, scheduling work after device teardown if privacy state is not deactivated elsewhere, missed privacy events when `alt` or `elid` filtering changes, and platform-specific core counts diverging between PTL and WCL. Test signals are IPC4 capability negotiation, SoundWire privacy mask programming with the expected DDZLS mask, IRQ-to-workqueue-to-firmware notification flow, suspend/remove cancellation behavior in adjacent HDA code, and successful boot on 5-core PTL and 3-core WCL variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/ptl.c -->
