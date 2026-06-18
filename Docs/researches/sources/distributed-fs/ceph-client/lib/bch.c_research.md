<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bch.c -->
# sources/distributed-fs/ceph-client/lib/bch.c

## Purpose
Implements a runtime-configurable binary BCH error-correction library. It can generate ECC parity bytes, decode data/ECC syndromes, and locate bit errors for callers such as NAND flash drivers.

## APIs, Types, and Functions
Exports `bch_init()`, `bch_encode()`, `bch_decode()`, and `bch_free()`. Key internal types include `struct gf_poly` and `struct gf_poly_deg1`; public state is in `struct bch_control` from `linux/bch.h`. Internal helpers cover bit swapping, ECC byte/word conversion, Galois field arithmetic, syndrome computation, Berlekamp-Massey error locator generation, low-degree root solvers, Berlekamp Trace factorization, optional Chien search, generator polynomial construction, GF table construction, mod-8 encoding table construction, and degree-2 base generation.

## Control Flow, State, and Persistence
`bch_init()` validates `m` and `t`, optionally enforces `CONFIG_BCH_CONST_PARAMS`, chooses or validates a primitive polynomial, allocates tables/buffers, builds GF log/power tables, computes the generator polynomial, builds encoding lookup tables, and prepares root-solving bases. `bch_encode()` loads existing ECC or clears it, processes unaligned bytes, then aligned 32-bit words through four precomputed mod-8 tables, and stores parity bytes. `bch_decode()` accepts raw data plus received ECC, received/calculated ECC, XORed ECC, or hardware syndromes; it computes syndromes if needed, builds the error locator polynomial, finds roots, and maps raw roots into caller-facing bit locations. `bch_free()` releases all allocations. State persists in the allocated `bch_control` and is intended to be initialized during driver setup, not fast paths.

## Dependencies and Integration
Depends on kernel allocation, bit operations, bit reversal, byteorder helpers, `linux/bch.h`, Kconfig options `BCH`, `BCH_CONST_PARAMS`, `BCH_CONST_M`, and `BCH_CONST_T`. NAND/MTD ECC engines and other storage code integrate by keeping a `bch_control`, calling encode/decode for page data, and correcting returned bit locations themselves.

## Risks and Test Signals
Risks include parameter mismatch under constant-parameter builds, stack/table bounds for large `m*t`, primitive polynomial validity, caller interpretation of data-vs-ECC error locations, bit order controlled by `swap_bits`, and performance cost of initialization. This snapshot contains suspicious duplicated source text in the degree-2 root path, making compile and algorithm regression tests especially important. Test signals include known BCH vectors for multiple `(m,t)`, NAND page ECC correction up to `t` bits, uncorrectable error returns, `swap_bits` variants, hardware syndrome input, invalid parameter rejection, allocation-failure cleanup, and comparison against Chien-search/reference implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bch.c -->
