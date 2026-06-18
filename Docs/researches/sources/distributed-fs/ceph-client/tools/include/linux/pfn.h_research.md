<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/pfn.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/pfn.h

## Purpose
`pfn.h` provides page frame number conversion macros for tools.

## APIs And Flow
It includes `linux/mm.h` and defines `PFN_UP()`, `PFN_DOWN()`, `PFN_PHYS()`, and `PHYS_PFN()`. Flow is shift and add arithmetic based on `PAGE_SHIFT` and `PAGE_SIZE`.

## State, Dependencies, Risks, Tests
There is no state. Dependencies are the page constants and `phys_addr_t` from the tools MM/type layer. Risks are overflow in `PFN_UP(x)` near address maxima, fixed page-size assumptions, and accidental use for real kernel physical memory semantics. Tests should cover aligned and unaligned addresses, zero, max safe values, and round-trip `PFN_PHYS(PHYS_PFN(x))` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/pfn.h -->
