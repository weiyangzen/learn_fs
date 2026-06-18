<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom-soc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom-soc.yaml

## Purpose
This schema enforces Qualcomm SoC-compatible naming conventions for component nodes rather than a specific hardware block.

## Important APIs, Types, And Functions
The `select` matches Qualcomm compatible strings containing SoC families such as APQ, IPQ, MDM, MSM, QCM, QCS, QRU/QDU, SA, SC, SDM/SDA/SDX/SM, X1E/X1P, plus names like Glymur and Milos. The allowed `compatible` patterns prefer `qcom,SoC-IP` format while preserving legacy wildcard and enum exceptions.

## Control Flow
When selection matches a compatible string, validation checks it against preferred patterns, legacy patterns, or explicit exceptions. `additionalProperties: true` means the schema only polices naming.

## State And Persistence
There is no hardware state. The schema persists naming policy in machine-readable form.

## Dependencies And Integration Points
It integrates with every Qualcomm component binding by adding a cross-cutting dt-schema naming check.

## Risks
Overly broad regex changes can reject valid legacy compatibles or accept new names that violate policy. New legacy exceptions should be rare and explicit.

## Test Signals
`dt_binding_check` and `dtbs_check` surface naming violations for Qualcomm component nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/qcom-soc.yaml -->
