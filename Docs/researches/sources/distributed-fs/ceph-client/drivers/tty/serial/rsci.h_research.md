# sources/distributed-fs/ceph-client/drivers/tty/serial/rsci.h

## Purpose

`rsci.h` is the small public header connecting the RSCI implementation with the shared SH-SCI serial driver. It declares the RSCI OF data objects that other SH-SCI code can reference when matching Renesas RSCI-compatible devices.

## Important APIs, Types, and Functions

The header includes `sh-sci-common.h` so `struct sci_of_data` is available, then declares `extern struct sci_of_data of_rsci_rzg3e_data`, `of_rsci_rzg3l_data`, and `of_rsci_rzt2h_data`. These objects are defined in `rsci.c` and describe the RSCI port operations, UART operations, FIFO parameters, error masks, and type identifiers for the supported SoC families.

## Control Flow

There is no executable control flow in the header. Its role is compile-time linkage: files that include it can bind OF match entries or common driver tables to the RSCI-specific data blocks exported by `rsci.c`.

## State and Persistence Behavior

The header owns no state and has no persistence behavior. State associated with the declared objects is static data in `rsci.c`.

## Dependencies and Integration Points

The dependency is the SH-SCI common header. The integration point is the common Renesas serial framework's OF data plumbing: RSCI support is kept in a separate C file while the declarations allow shared code to reference its per-compatible descriptors.

## Risks and Edge Cases

The main risk is declaration/definition drift: if an exported `sci_of_data` object is renamed or conditionally removed in `rsci.c`, users of this header will fail to link. The include guard prevents double inclusion, and the header intentionally contains no inline behavior or register definitions.

## Test Signals

Build tests should cover configurations that compile RSCI support together with SH-SCI common code, including early console configurations. Link failures around the three declared OF data objects would be the primary signal of header/API drift.
