# sources/distributed-fs/ceph-client/arch/s390/include/asm/pci_debug.h

Purpose: This header provides zPCI debug-feature logging wrappers.

Important APIs/types/functions: `pci_debug_msg_id`, `pci_debug_err_id`, `zpci_dbg()`, `zpci_err()`, `zpci_err_hex_level()`, and `zpci_err_hex()` are defined.

Control flow: zPCI code writes formatted messages to the normal debug area and text or binary data to the error debug area.

State and persistence: Persistent state is held by `debug_info_t` debug feature instances allocated by zPCI debug initialization.

Dependencies and integration points: It depends on s390 `asm/debug.h` and integrates with zPCI core, error handling, and debugfs/debug feature tooling.

Risks and test signals: The fixed 16-byte text buffer in `zpci_err()` truncates messages, so callers should keep text concise. Tests should cover debug init/exit, message/error logging, hex dumps, and disabled debug feature behavior.
