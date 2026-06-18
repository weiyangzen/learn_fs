<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.c

## Purpose
`smsir.c` integrates Siano firmware IR sample indications with the Linux rc-core raw IR stack. It allocates an rc device per Siano core device, configures the keymap from board data, and forwards raw pulse/space durations from firmware into rc-core.

## Important APIs, Types, and Functions
The public functions are `sms_ir_init()`, `sms_ir_exit()`, and `sms_ir_event()`. `sms_ir_init()` allocates `RC_DRIVER_IR_RAW`, sets names/physical path/parent, allowed protocols, map name, driver name, and registers the rc device. `sms_ir_event()` interprets the payload as signed 32-bit samples and stores `ir_raw_event` entries. `sms_ir_exit()` unregisters and frees the rc device.

## Control Flow
`smscore_start_device()` calls IR initialization when board configuration advertises an IR port, then sends `MSG_SMS_START_IR_REQ`. Later, `smscore_onresponse()` routes `MSG_SMS_IR_SAMPLES_IND` to `sms_ir_event()`, which converts each sample into duration plus pulse flag and calls `ir_raw_event_handle()`.

## State and Persistence Behavior
State lives in `coredev->ir`: rc device pointer, human-readable name, physical path, timeout, controller, and keymap. There is no persistence; rc-core owns runtime input-device registration after `rc_register_device()`.

## Dependencies and Integration Points
The file depends on `smscoreapi.h`, `sms-cards` for board names and rc maps, and Linux input/rc-core. It is conditionally exposed by `smsir.h` through `CONFIG_SMS_SIANO_RC`.

## Risks and Test Signals
`sms_ir_exit()` calls both `rc_unregister_device()` and `rc_free_device()` on `coredev->ir.dev`; rc-core ownership conventions should be checked for the target kernel version to avoid double-free concerns. `sms_ir_event()` assumes payload length is a multiple of four bytes and that negative samples represent pulses. Test signals include rc device creation with the expected name/path, decoded remote events from firmware samples, safe unload when IR was not initialized, and no events after device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.c -->
