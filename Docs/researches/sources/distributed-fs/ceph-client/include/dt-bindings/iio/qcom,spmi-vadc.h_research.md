# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-vadc.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi vadc so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 256 macro constants. Representative symbols are `VADC_USBIN`, `VADC_DCIN`, `VADC_VCHG_SNS`, `VADC_SPARE1_03`, `VADC_USB_ID_MV`, `VADC_VCOIN`, `VADC_VBAT_SNS`, `VADC_VSYS`, `VADC_DIE_TEMP`, `VADC_REF_625MV`. numeric values span 0..255 across 256 direct numeric defines. Top naming groups: `VADC_LR` (44), `VADC_P` (32), `ADC7_AMUX` (24), `ADC5_AMUX` (20), `ADC5` (11).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with Qualcomm SPMI ADC/VADC bindings, PMIC DTS files, thermal/charger/battery consumers, and the qcom-spmi ADC drivers that decode channel ids and scaling selectors.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Channel-id drift or duplicated offsets can make battery, charger, die-temperature, or GPIO-ratio measurements read the wrong PMIC input.

## Test Signals
dtbs_check plus PMIC ADC driver probe tests should cover representative channel ids, ADC mux variants, thermal zone consumers, and scale/pre-scaling expectations.
