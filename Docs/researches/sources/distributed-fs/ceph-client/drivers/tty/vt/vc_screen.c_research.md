# sources/distributed-fs/ceph-client/drivers/tty/vt/vc_screen.c

## Purpose
`vc_screen.c` implements the `/dev/vcs`, `/dev/vcsN`, `/dev/vcsaN`, and `/dev/vcsuN` character devices that expose virtual console screen memory to user space. It supports foreground-console proxy minors, glyph and attribute formats, Unicode screen reads, writes to glyph/attribute devices, polling/fasync for VT updates, and sysfs device creation/removal.

## Important APIs, Types, And Functions
- Minor decoding macros split console number, Unicode mode, and attribute mode.
- `struct vcs_poll_data` stores a VT notifier, wait queue, fasync state, event code, and console number.
- `vcs_vc()` resolves an inode to a `vc_data` under `console_lock`.
- `vcs_size()` calculates visible file size for glyph, attribute, and Unicode modes.
- File operations are `vcs_lseek()`, `vcs_read()`, `vcs_write()`, `vcs_poll()`, `vcs_fasync()`, `vcs_open()`, and `vcs_release()`.
- Buffer helpers include `vcs_read_buf_uni()`, `vcs_read_buf_noattr()`, `vcs_read_buf()`, `vcs_write_buf_noattr()`, and `vcs_write_buf()`.
- Device lifecycle APIs are `vcs_make_sysfs()`, `vcs_remove_sysfs()`, and `vcs_init()`.

## Control Flow And State
`vcs_init()` registers major `VCS_MAJOR`, registers class `vc`, creates the foreground proxy devices, and creates devices for initially allocated consoles. Open rejects Unicode-with-attributes minors and nonallocated numbered consoles. Reads allocate one page, take `console_lock`, verify size and alignment, copy screen data into the page while locked, drop the lock for `copy_to_user()`, then reacquire and continue because console state may change while copying. Unicode reads require 4-byte aligned position/count and call `vc_uniscr_check()` before copying lines through `vc_uniscr_copy_line()`.

Writes reject Unicode minors, copy user data into a temporary page outside the console lock, revalidate the VC and size, then update screen memory under the lock. Attribute-mode writes may update the 4-byte header cursor position for background consoles and write native-endian attribute/character words; glyph-only writes preserve attributes. Updated regions are redrawn with `update_region()` and update notifiers are emitted through `vcs_scr_updated()`.

## State And Persistence Behavior
Persistent device state is per-open `file->private_data` for poll/fasync. It is lazily allocated and registered with the VT notifier list, protected from races by `file->f_lock`, and freed on release. Screen contents live in `vc_data`, not in this file. Reads and writes observe live console state and may return partial progress if the VC disappears or size changes.

## Dependencies And Integration Points
The file depends on the VT core (`vc_cons`, `fg_console`, `vc_cons_allocated`, `update_region`, Unicode side-buffer helpers, screen accessors), selection state for clean screen dumping, keyboard/console headers, Linux char-device/file/poll/fasync infrastructure, user-copy APIs, and notifier chains. It receives `VT_UPDATE` and `VT_DEALLOCATE` from `vt.c` to drive `poll()` and `SIGIO`.

## Risks And Edge Cases
The minor space assumes `MAX_NR_CONSOLES <= 63`; the file emits a preprocessor warning otherwise. Unicode attributes are explicitly unsupported. Unicode read alignment is strict. The foreground proxy minor follows `fg_console` dynamically, so reads can observe different consoles across calls. Copying to or from user requires dropping `console_lock`, so every loop revalidates size and allocation. Poll state allocation can race across threads sharing a file descriptor and is carefully collapsed to one survivor.

## Test Signals
Test opening `/dev/vcs`, `/dev/vcs1`, `/dev/vcsa1`, `/dev/vcsu`, and unsupported Unicode+attribute minors. Verify lseek sizes, 4-byte Unicode alignment errors, header row/column/cursor bytes, glyph-only reads preserving attributes, writes updating screen memory and redraws, poll returning `POLLPRI` on updates and `POLLHUP` on deallocate, fasync `SIGIO`, foreground proxy behavior across VT switches, and sysfs device creation/removal as consoles allocate/deallocate.
