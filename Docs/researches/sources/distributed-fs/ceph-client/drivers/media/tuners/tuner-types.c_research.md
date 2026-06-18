# sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-types.c

Purpose: static tuner database for simple tuner cans: names, frequency ranges, config/control bytes, IFs, digital step sizes, init/sleep data, and TDA9887-related flags.

APIs/data: exports `tuners[]` and `tuner_count`. Defines many `tuner_range` and `tuner_params` arrays for PAL/NTSC/SECAM/radio/digital variants, plus AGC init arrays such as `tua603x_agc103` and `tua603x_agc112`.

Control flow/state: no active runtime code beyond exports. `tuner-simple.c` selects `tuners[type]`, chooses a params entry, finds a range by target frequency, and converts the data into I2C payloads.

Dependencies/integration: `media/tuner.h` and `media/tuner-types.h`; special entries point users to separate drivers such as TEA576x, XC2028, XC4000, XC5000, TDA8290, TDA9887, and SI2157.

Risks/tests: wrong table bytes or enum mapping retune hardware incorrectly. Test table compile coverage, boundary range lookup, digital min/max/stepsize/IF values, and known board regressions after edits.
