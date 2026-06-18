# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm8350b.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi adc7 pm8350b so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 62 macro constants. Representative symbols are `PM8350B_SID`, `PM8350B_ADC7_REF_GND`, `PM8350B_ADC7_1P25VREF`, `PM8350B_ADC7_VREF_VADC`, `PM8350B_ADC7_DIE_TEMP`, `PM8350B_ADC7_AMUX_THM1`, `PM8350B_ADC7_AMUX_THM2`, `PM8350B_ADC7_AMUX_THM3`, `PM8350B_ADC7_AMUX_THM4`, `PM8350B_ADC7_AMUX_THM5`. numeric values span 3..3 across 1 direct numeric defines. Top naming groups: `PM8350B_ADC7` (61), `PM8350B` (1).

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
