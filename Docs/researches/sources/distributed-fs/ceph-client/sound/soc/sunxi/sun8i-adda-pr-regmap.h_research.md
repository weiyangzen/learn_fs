# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun8i-adda-pr-regmap.h

## Purpose
This header declares the ADDA PR regmap factory used to access Allwinner analog audio codec registers through a PRCM bridge register.

## Important APIs, types, and functions
The single API is `struct regmap *sun8i_adda_pr_regmap_init(struct device *dev, void __iomem *base);`. It returns a devm-managed regmap or an error pointer. The declaration assumes users include appropriate kernel declarations for `struct device`, `void __iomem`, and `struct regmap` through their source includes.

## Control flow
There is no executable control flow in the header. Consumers call the initializer after mapping the PRCM/analog register resource and pass the mapped base address into the helper.

## State and persistence
The header owns no state. Persistence semantics are defined by the implementation's regmap and the consumer driver's device-managed lifetime.

## Dependencies and integration points
`sun8i-codec-analog.c` includes this header and calls the initializer during platform probe. The declaration is paired with the GPL-exported implementation in `sun8i-adda-pr-regmap.c`.

## Risks and edge cases
The header has no include guard and no forward declarations, so it relies on current include order. Multiple inclusion is currently harmless because it only contains one compatible function declaration, but adding types or inline helpers later would require a guard.

## Test signals
Compile coverage is the primary signal: any missing declaration, include-order problem, or signature drift between the header and implementation will fail builds of analog codec users.
