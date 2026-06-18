# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,s2mps11.h

## Purpose
`samsung,s2mps11.h` defines clock IDs for fixed-rate clocks provided by the Samsung S2MPS11 PMIC.

## Important APIs, types, and functions
The macro API is `S2MPS11_CLK_AP`, `S2MPS11_CLK_CP`, `S2MPS11_CLK_BT`, and `S2MPS11_CLKS_NUM`. There are no functions or structs.

## Control flow
DTS consumers reference a PMIC clock phandle with one of these IDs. The S2MPS11 clock provider returns the corresponding fixed-rate or PMIC-controlled output clock to consumers.

## State and persistence
The header is stateless. PMIC register configuration and physical board routing determine whether AP, CP, or BT consumers receive usable clocks.

## Dependencies and integration points
It integrates with S2MPS11 MFD/PMIC support, Samsung board DTS files, common clock framework fixed-rate outputs, and modem/Bluetooth/application-processor clock consumers.

## Risks and test signals
Risks include swapped AP/CP/BT indexes and incorrect `S2MPS11_CLKS_NUM` if outputs are extended. Test signals include PMIC clock provider registration, consumer probe success, and measured or debugfs-visible fixed clock outputs.
