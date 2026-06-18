<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/primecell.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/primecell.yaml

## Purpose
This generic schema describes ARM PrimeCell peripherals that expose standard ID registers for driver matching.

## Important APIs, Types, And Functions
The compatible list must contain `arm,primecell` after a more specific engineering-name compatible. Optional properties include `arm,primecell-periphid`, `clocks`, and `clock-names` containing `apb_pclk`.

## Control Flow
Validation checks that `arm,primecell` appears in the compatible list and that clock naming includes the APB clock. Additional properties are allowed for specific PrimeCell device bindings.

## State And Persistence
The DT records peripheral identity, optional ID override, and clock inputs. Runtime state is managed by the specific PrimeCell driver.

## Dependencies And Integration Points
It is a shared integration point for many ARM AMBA/PrimeCell device schemas and drivers.

## Risks
Because additional properties are allowed, specific device schemas must add stricter validation. Wrong `arm,primecell-periphid` can override hardware identification incorrectly.

## Test Signals
`dtbs_check` validates common PrimeCell constraints; AMBA bus probing and specific driver binding validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/primecell.yaml -->
