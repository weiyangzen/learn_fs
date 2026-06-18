# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hw.c

## Purpose
`qed_hw.c` is the low-level hardware access layer for the QLogic/Marvell QED driver. It manages PTT BAR windows, register reads and writes, pretend addressing for PF/VF/port access, DMAE command execution, DMAE resource lifetime, hardware error notification, and a DMAE self-test path.

## Important APIs, Types, and Functions
- `struct qed_ptt` tracks a PTT list node, external BAR window index, cached PXP entry, and owning hwfn id.
- `struct qed_ptt_pool` owns the free PTT list and a spinlock-protected array of external BAR windows.
- `qed_ptt_pool_alloc()` and `qed_ptt_pool_free()` allocate/free PTT state, reserving indices below `RESERVED_PTT_MAX`.
- `qed_ptt_acquire_context()` polls for a free PTT using `udelay()` in atomic context or `usleep_range()` otherwise; `qed_ptt_release()` returns it to the free list.
- `qed_wr()`, `qed_rd()`, `qed_memcpy_from()`, and `qed_memcpy_to()` are the core GRC/BAR access helpers.
- `qed_fid_pretend()`, `qed_port_pretend()`, `qed_port_unpretend()`, and `qed_port_fid_pretend()` program the PXP pretend fields in a PTT entry.
- `qed_dmae_info_alloc()` and `qed_dmae_info_free()` allocate coherent completion, command, and intermediate DMA buffers.
- `qed_dmae_host2grc()`, `qed_dmae_grc2host()`, and `qed_dmae_host2host()` serialize DMAE transfers through `p_hwfn->dmae_info.mutex`.
- `qed_hw_err_notify()` reports hardware errors to recovery logic and management firmware debug data.
- `qed_dmae_sanity()` tests host-to-host DMAE correctness with a known memory pattern.

## Control Flow
Register access flows through `qed_set_ptt()`: the helper checks whether the requested GRC address is within the cached BAR window, retargets the window with `qed_ptt_set_win()` when needed, and returns the BAR-relative address for `REG_RD/REG_WR`. Block copies iterate in chunks no larger than one PXP external BAR window; PFs retarget the PTT for each chunk, while VFs use the supplied address directly.

DMAE operations build an opcode in `qed_dmae_opcode()`, populate command memory with source/destination addresses in `qed_dmae_execute_sub_operation()`, post command words to `DMAE_REG_CMD_MEM`, trigger the per-channel go register, and poll the coherent completion word. Large transfers split at `DMAE_MAX_RW_SIZE`; virtual host buffers are copied through the coherent intermediate buffer.

## State and Persistence
Persistent driver state lives under `p_hwfn`: PTT pool allocation, cached PTT PXP offsets/pretend fields, DMAE coherent buffers, completion word, intermediate buffer, and selected DMAE channel. Hardware-visible state includes PXP window mappings, PXP pretend command fields, DMAE command memory, DMAE go registers, and error/recovery notifications. No disk persistence is involved.

## Dependencies and Integration Points
This file depends on Linux MMIO, DMA mapping, spinlocks, mutexes, PCI device state, QED register definitions, HSI structures, SR-IOV helpers, and management firmware hooks. It is used broadly by initialization, interrupts, context setup, storage offloads, SPQ, debug, and L2 paths that need direct register or internal RAM access.

## Risks
- PTT misuse across hwfns is detected only by logging; a wrong PTT can target the wrong BAR window.
- DMAE waits are bounded but busy-poll with `udelay()` and can return `-EBUSY` on device or firmware failure.
- `qed_dmae_execute_sub_operation()` ignores the return value from `qed_dmae_post_command()`, so invalid command detection depends on later wait behavior in normal paths.
- Virtual host DMAE paths use an intermediate buffer protected by one mutex; callers must not bypass that serialization.
- Pretend state persists in the PTT until overwritten, so callers must intentionally restore/replace function or port identity.

## Test Signals
Useful validation includes successful `qed_dmae_sanity()` during init callbacks, no PTT acquire timeouts under stress, register read/write traces in `NETIF_MSG_HW`, absence of DMAE timeout notices, correct SR-IOV pretend behavior, and hardware recovery events from `qed_hw_err_notify()` when DMAE or attention paths fail.
