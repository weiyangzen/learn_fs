<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/uvesafb.h -->
# sources/distributed-fs/ceph-client/include/video/uvesafb.h

## Purpose
This header defines the uvesafb kernel-side VBE/VESA structures, mode flags, userspace task wrapper, palette entry, mode-selection flags, and driver-private state.

## Important APIs, Types, And Functions
- `struct vbe_crtc_ib` models a packed VBE CRTC info block with horizontal/vertical timing, flags, pixel clock, and refresh rate.
- `struct vbe_mode_ib` models a packed VBE mode info block covering VBE 1.0 through 3.0 fields, including windowing, resolution, memory model, direct color masks, linear framebuffer address, image pages, max pixel clock, mode ID, and depth.
- `VBE_MODE_*` and `VBE_MODE_MASK` identify supported color graphics linear-framebuffer modes.
- `UVESAFB_DEFAULT_MODE`, `UVESAFB_TIMEOUT`, and `UVESAFB_TASKS_MAX` define fallback mode, userspace reply timeout, and concurrency limit.
- `struct uvesafb_pal_entry` and DAC port constants support palette programming.
- `struct uvesafb_ktask` wraps a UAPI task with buffer, completion, and acknowledgement.
- `struct uvesafb_par` stores VBE info, mode list, CRTC data, PMI state, original/saved VBE state, refcount, selected mode, MTRR handle, and ypan behavior.

## Control Flow
The driver asks userspace to execute VBE BIOS calls via `uvesafb_ktask`, waits up to `UVESAFB_TIMEOUT`, parses mode blocks, selects a mode by exact-resolution/depth flags, optionally applies CRTC settings, maps the linear framebuffer, saves original state, and restores saved/original state during suspend or unload.

## State And Persistence
Persistent driver state includes VBE mode tables, saved BIOS state, PMI pointers, current mode index, CRTC settings, MTRR registration, and atomic reference count. Hardware state is in VBE firmware-controlled video registers and DAC palette.

## Dependencies And Integration Points
It depends on `uapi/video/uvesafb.h`, completion/atomic primitives in implementation, userspace helper infrastructure, VBE BIOS, fbdev, MTRR support, and x86/VESA-compatible firmware.

## Risks And Edge Cases
Packed structures must match VBE ABI exactly. Userspace helper timeouts or bad acknowledgements block mode setup. `nocrtc`, `ypan`, and PMI palette flags change hardware paths and need validation. Mode blocks from firmware can be malformed or unsupported despite advertised attributes.

## Test Signals
Signals include successful helper round trips, valid mode list parsing, exact resolution/depth selection, framebuffer mapping at `phys_base_ptr`, palette updates with and without PMI, ypan/ywrap behavior, saved state restoration, and timeout/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/uvesafb.h -->
