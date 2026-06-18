# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_mmu.c

## Purpose
Implements 64-bit Book3S PR guest hash-MMU translation and SLB emulation. It decodes guest SLB entries, locates guest HPTEs, computes guest physical addresses and permissions, updates guest reference/change bits, and installs the 64-bit Book3S PR MMU callback table.

## Important APIs, Types, And Functions
Major helpers include `kvmppc_mmu_book3s_64_find_slbe`, `kvmppc_slb_calc_vpn`, `kvmppc_mmu_book3s_64_get_pteg`, `kvmppc_mmu_book3s_64_get_avpn`, `decode_pagesize`, `kvmppc_mmu_book3s_64_xlate`, `kvmppc_mmu_book3s_64_slbmte`, `slbfee`, `slbmfee`, `slbmfev`, `slbie`, `slbia`, `mtsrin`, `tlbie`, `esid_to_vsid`, `ea_to_vp`, `is_dcbz32`, and `kvmppc_mmu_book3s_64_init`.

## Control Flow
Translation checks the magic page, finds a matching 256 MiB or 1 TiB SLB entry, constructs the AVPN and HPTE search mask, locks the VM HPT mutex, scans primary then secondary guest PTEGs, decodes page size and permission bits, computes RPN plus effective-address offset, and writes R/C bits back with single-byte updates. SLB instructions mutate the emulated SLB array and trigger shadow segment mapping or flushing. `tlbie` computes a vpage flush mask based on processor generation and large-page encoding and flushes all vCPUs.

## State And Persistence
State is per-vCPU SLB entries, SDR1, hflags, HID bits, magic page data, and callback function pointers. Guest HPTE R/C updates persist into guest memory. Shadow segment mappings are maintained in the host PR MMU layer.

## Dependencies And Integration Points
Depends on Book3S 64 hash MMU definitions, HPT hash helpers, guest memory copy helpers, PR host MMU mapping in `book3s_64_mmu_host.c`, and common Book3S translation wrappers. It supports PAPR guests where SDR1 may contain an HVA rather than a GPA.

## Risks And Edge Cases
The source snapshot contains questionable duplicated assignment (`key = 4`) and a debug print referencing `page` outside the visible local declaration, which are correctness/compile risks if active. Mixed page-size decoding is limited. SLB bounds checks use slot numbers from guest registers and must prevent array overflow. R/C updates race with guest HPTE modification but intentionally mimic hardware byte writes. Magic-page translation depends on correct segment fallback when no SLB exists.

## Test Signals
Boot 64-bit PR hash guests, exercise 4K/64K/16M mappings, primary/secondary HPT lookup, SLB insert/remove/all-invalidate, `mtsrin`, `tlbie` old and POWER6+ encodings, PAPR SDR1 HVA mode, magic page access, NX/disable-kernel-NX behavior, and dirty/reference bit observation by guest OS.
