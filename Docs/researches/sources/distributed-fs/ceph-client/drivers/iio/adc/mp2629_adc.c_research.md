# sources/distributed-fs/ceph-client/drivers/iio/adc/mp2629_adc.c

Purpose: this platform driver exposes the ADC block inside the MPS MP2629 charger MFD as an IIO direct-mode device. It provides battery/system/input voltage and battery/input current channels and registers IIO maps so the sibling `mp2629_charger` consumer can find named measurements.

Important APIs, types, and functions: `struct mp2629_adc` holds the parent regmap and device pointer. `MP2629_ADC_CHAN()` defines five simple channel specs with raw and type-shared scale information. `mp2629_read_raw()` reads one register through `regmap_read()`, masks the input-voltage status bit, and returns hard-coded per-channel scales. `mp2629_adc_probe()` obtains `struct mp2629_data` from the parent MFD, enables `MP2629_ADC_START | MP2629_ADC_CONTINUOUS`, registers IIO maps, and then registers the IIO device. `mp2629_adc_remove()` reverses IIO registration and clears continuous/start bits.

Control flow: probe is linear: allocate IIO state, bind the parent regmap, enable continuous ADC conversion, publish consumer maps, set channel metadata, and register with IIO. Raw reads are passive because conversions are already running. Error paths unregister maps and disable the ADC bits.

State and persistence: driver state is per-device and devm allocated. Persistent hardware state is limited to the ADC control register while the platform device is bound. There is no buffering, IRQ handling, runtime PM, or disk persistence.

Dependencies and integration points: it depends on the MP2629 MFD parent regmap, platform/OF binding `mps,mp2629_adc`, IIO core registration, and IIO machine maps consumed by charger code.

Risks: probe assumes the parent MFD driver data is valid. Raw reads trust continuously updated single-byte registers with no conversion-ready check. Remove and failure paths clear `START` separately from `CONTINUOUS`, so regmap failures during cleanup are ignored. Incorrect scales or register masks directly affect charger policy consumers.

Test signals: validate probe under the MP2629 MFD, IIO map lookup by the charger, raw reads for all five channels, scale values and `IIO_VAL_FRACTIONAL` current scaling, input-voltage masking, and cleanup that clears ADC enable bits on unregister.
