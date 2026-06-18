# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_routing/ni_device_routes/all.h

## Purpose

`ni_device_routes/all.h` is the generated extern catalog for all generated per-board NI valid-route tables. It centralizes declarations so `ni_device_routes.c` can build the global lookup list without each board file needing a bespoke header.

## Important APIs, Types, and Functions

The file declares `extern struct ni_device_routes` symbols for E-series, M-series, 653x, 6602, 6713/6723/6733, PXI, and PXIe route tables. Examples include `ni_pxi_6030e_device_routes`, `ni_pci_6070e_device_routes`, `ni_pci_6220_device_routes`, `ni_pci_6259_device_routes`, `ni_pci_6534_device_routes`, `ni_pxie_6535_device_routes`, and `ni_pxie_6738_device_routes`.

It defines no functions. The declarations rely on `../ni_device_routes.h`, which in turn includes the core route type definitions from `ni_routes.h`.

## Control Flow, State, and Persistence

The header has no runtime control flow or storage. It is generated metadata used at compile time to tie per-board C translation units to the central route-list translation unit.

## Dependencies and Integration Points

`ni_device_routes.c` includes this file to reference board symbols. Each generated board `.c` file also includes `all.h`, which gives the compiler visibility into sibling table symbols if generator output ever needs them. The generator in `ni_routing/tools/convert_csv_to_c.py` is the likely source of this extern list and should be used to maintain it.

## Risks and Test Signals

The main integration risk is mismatch between this extern catalog, `ni_device_routes.c`, and the Makefile. In this snapshot the catalog declares `ni_pxie_6535_device_routes` and `ni_pxie_6738_device_routes`; the Makefile builds those objects; but the central `ni_device_routes_list[]` omits them. A consistency test should assert that every generated table intended for assignment appears in the central registry or is documented as reachable by an alternate board name.

Build success catches missing object definitions for externs only when they are actually referenced. Runtime assignment tests are still required to catch externs that compile but are not in the lookup list.
