# sources/distributed-fs/ceph-client/include/net/nfc/nfc.h

Purpose: defines the generic kernel NFC device API used by digital, HCI, NCI, and controller drivers to expose polling, target activation, DEP, secure element, firmware, and vendor-command functionality.

Important APIs and types: `struct nfc_ops` is the main driver callback table. `struct nfc_target` describes discovered peer identifiers and activation data. `struct nfc_se` and `struct nfc_evt_transaction` model secure elements and SE transactions. `struct nfc_vendor_cmd` supports vendor netlink commands. `struct nfc_dev` stores target lists, device model state, polling/active target flags, DEP state, rfkill, generic netlink command context, secure elements, vendor commands, check-presence work/timer, and ops.

Control flow: drivers allocate/register `nfc_dev`; userspace netlink operations call ops; drivers report target discovery/loss, DEP link state, target-mode data, firmware completion, secure element events, and driver failures back to core helpers.

State and persistence: all state is kernel runtime device state. Secure element list and target generations are not persistent; controller firmware may persist outside this API.

Dependencies and integration points: depends on Linux NFC UAPI, device model, skbuffs, rfkill, generic netlink, timers/work, raw NFC sockets, and upper stack wrappers.

Risks and test signals: risks include active target lifetime, vendor reply misuse outside `doit()`, concurrent polling/dev_down, rfkill teardown, and check-presence races. Test registration/unregistration, polling, activation/deactivation, DEP link up/down, transceive callbacks, SE add/remove/transaction, firmware completion, raw socket tap, and vendor command replies.
