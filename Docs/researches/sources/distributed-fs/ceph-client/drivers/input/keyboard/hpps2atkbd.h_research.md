## sources/distributed-fs/ceph-client/drivers/input/keyboard/hpps2atkbd.h

Purpose: HP PA-RISC PS/2 AT keyboard raw set-2 scancode table consumed by the AT keyboard path. It maps normal and escaped PS/2 scancodes to Linux `KEY_*` codes for HP workstation and laptop layouts.

Important APIs/types/functions: this header does not define functions or storage wrappers; it is an initializer fragment. `CONFLICT()` and the temporary `C_*` macros choose between HP and RDI PrecisionBook mappings depending on `CONFIG_KEYBOARD_ATKBD_RDI_KEYCODES`.

Control flow: inclusion context supplies the target array declaration. The header expands into two contiguous 256-entry-style tables: base set-2 scancodes followed by escaped-key offsets. Conditional conflict macros adjust keys such as F12/F1, left alt/control, caps/control, and 102nd/left.

State/dependencies/integration: no runtime state exists. It depends on the input keycode namespace and the including keyboard driver using the table shape correctly. Integration is compile-time only, with `#undef` cleanup for the temporary macros.

Risks and test signals: because it is an initializer fragment, table length/order is the contract. Off-by-one edits, missing escaped entries, or changing `CONFIG_KEYBOARD_ATKBD_RDI_KEYCODES` behavior can silently remap many physical keys. Test by booting both HP and RDI layout configurations, checking representative conflict keys and escaped cursor/navigation keys.
