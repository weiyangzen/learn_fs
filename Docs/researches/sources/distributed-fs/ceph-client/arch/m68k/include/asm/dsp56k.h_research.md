<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dsp56k.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/dsp56k.h

## Purpose
This header defines the user-facing ioctl data structures and command numbers for the Atari Falcon DSP56001/DSP56K device driver.

## Important APIs, Types, And Functions
- `struct dsp56k_upload` carries a byte length and user pointer to DSP binary code.
- `struct dsp56k_host_flags` carries host flag write direction bits, output values, and returned status.
- Ioctl command codes include `DSP56K_UPLOAD`, `DSP56K_SET_TX_WSIZE`, `DSP56K_SET_RX_WSIZE`, `DSP56K_HOST_FLAGS`, and `DSP56K_HOST_CMD`.

## Control Flow
Userspace issues ioctls with these structures. The driver copies upload data, configures transmit/receive word sizes, reads/writes host flags, or triggers a host command.

## State And Persistence Behavior
Persistent state is in the DSP device and driver: uploaded program, configured word sizes, and host flag state. The structs are transient syscall payloads.

## Dependencies And Integration Points
It uses `__user` pointer annotation and integrates with the Atari DSP host interface defined in `atarihw.h` and the DSP character device driver.

## Risks And Edge Cases
Ioctl numbers are small raw constants rather than `_IO*` encoded commands. User pointer and length validation must be handled by the driver. Host command values are limited by hardware.

## Test Signals
Userspace DSP upload, TX/RX word size changes, host flag read/write, invalid pointer/length handling, and host command range tests validate the ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/dsp56k.h -->
