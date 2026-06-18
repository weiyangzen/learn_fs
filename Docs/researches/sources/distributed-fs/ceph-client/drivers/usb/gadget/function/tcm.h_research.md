# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/tcm.h

## Purpose
This header defines the shared state for the USB gadget target-core fabric function, supporting USB Attached SCSI Protocol (UASP) and Bulk-Only Transport (BOT) modes. It connects USB composite function state to Linux target-core sessions, portal groups, command objects, streams, and endpoint resources.

## Important APIs, types, and functions
`struct tcm_usbg_nexus` holds the target-core session. `struct usbg_tpg` represents a target portal group with mutex, tag, target port pointer, workqueue, `se_portal_group`, connection flag, nexus, port count, and function instance. `struct usbg_tport` stores WWPN identity and `se_wwn`. `struct usbg_cmd` combines USB command metadata, target-core `se_cmd`, work item, request pointer, data buffer, reference count, UAS IU fields, task-management fields, and BOT CSW fields. `struct uas_stream` groups per-stream IN/OUT/status requests and completion/hash linkage. `struct f_uas` embeds `struct usb_function`, endpoint pointers, UAS streams/hash, BOT status, and BOT request state.

## Control flow
The header has no executable flow, but it defines how implementation files manage commands: BOT and UAS requests are converted into `usbg_cmd`, queued to target-core through `se_cmd`, processed on a workqueue, and completed through endpoint-specific requests. UAS mode uses stream IDs and a hash table; BOT mode uses a single command/status flow and flags such as `USBG_BOT_CMD_PEND` and `USBG_BOT_WEDGED`.

## State and persistence
Runtime state spans target portal groups, sessions, command objects, request objects, stream completions, endpoint pointers, and function flags. No durable persistence is defined here; identity such as WWPN lives in memory and is tied to target-core configuration.

## Dependencies and integration points
The header depends on USB composite, UAS and USB storage protocol definitions, Linux target-core base/fabric APIs, krefs, hash tables, workqueues, and completions. `fuas_to_gadget()` links `struct f_uas` back to the active USB gadget. The structures are consumed by the TCM USB gadget function implementation.

## Risks and edge cases
Command lifetime is reference-counted and crosses USB completion, workqueue, and target-core completion contexts, so leaks and use-after-free are primary risks. Stream counts derive from SuperSpeed companion stream settings. BOT and UAS share `f_uas` but have different flags and endpoint assumptions, so mode transitions must reset the correct state. Fixed command buffer size `USBG_MAX_CMD` must be respected when unpacking CDBs.

## Test signals
Build the TCM USB gadget function, enumerate BOT and UAS altsettings, run SCSI I/O and task-management commands, stress disconnect during outstanding commands, test stream allocation and hash lookup, validate BOT wedge/error handling, and run target-core session teardown tests.
