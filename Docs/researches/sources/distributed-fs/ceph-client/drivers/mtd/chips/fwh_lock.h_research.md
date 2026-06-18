## sources/distributed-fs/ceph-client/drivers/mtd/chips/fwh_lock.h

Purpose: header-only helper for Intel Firmware Hub style block lock registers. It installs lock/unlock callbacks that write FWH lock-control registers located 4 MiB below the flash address window rather than issuing normal flash array lock commands.

Important APIs, types, and functions: `enum fwh_lock_state` models register values such as `FWH_UNLOCKED` and `FWH_DENY_WRITE`. `struct fwh_xxlock_thunk` carries the desired register value and visible `flstate_t`. `fwh_xxlock_oneblock()` performs one block operation. `fwh_lock_varsize()`, `fwh_unlock_varsize()`, and `fixup_use_fwh_lock()` integrate with MTD/CFI callbacks.

Control flow: command-set fixups call `fixup_use_fwh_lock()`, replacing `mtd->_lock` and `_unlock`. Range calls use `cfi_varsize_frob()` to validate region alignment and iterate blocks. Each block callback maps the target block to a lock-register address, gets exclusive chip access with `get_chip()`, writes the desired lock byte, restores the previous chip state, and calls `put_chip()`.

State and persistence: persistent state lives in hardware lock registers. Software state is limited to transient `flchip` state changes under the chip mutex.

Dependencies and integration points: intended to be included by CFI Intel-extension code. It depends on `cfi_varsize_frob()`, `get_chip()`, `put_chip()`, `map_write()`, and the CFI map geometry model.

Risks: comments explicitly state FWH parts are not interleaved and the code is likely wrong for interleaved chips. It refuses chips below 4 MiB to avoid underflow, but odd map offsets can still be hazardous. These are register writes with no status polling.

Test signals: lock and unlock on FWH/LPC firmware flash, correct register address calculation on 64 KiB boundaries, `-EIO` below the required address window, successful protection against writes after lock, and no regressions on non-FWH CFI parts where the fixup is absent.
