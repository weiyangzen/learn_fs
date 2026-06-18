# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-saif.h

Purpose: defines MXS SAIF register offsets, bit masks, helper macros, MCLK ID, driver state structure, and exported MCLK helper declarations.

Important APIs/types/functions: register groups include `SAIF_CTRL`, `SAIF_STAT`, `SAIF_DATA`, and `SAIF_VERSION`. `struct mxs_saif` stores device, clock, MCLK, MMIO base, IDs, rate, error counters, and state enum. Exports `mxs_saif_put_mclk` and `mxs_saif_get_mclk`.

Control flow: no executable flow, but macro definitions are directly used to compose control register writes in `mxs-saif.c`.

State and persistence: defines the persistent per-controller state used by the SAIF driver.

Dependencies and integration: includes `mxs-pcm.h` and is used by the SGTL5000 machine driver for MCLK APIs.

Risks: register bit definitions are hardware contract; incorrect masks can corrupt adjacent fields. The exposed `struct mxs_saif` makes implementation details visible to local compilation units.

Test signals: compile coverage, register programming validation on hardware, and SGTL5000 machine-driver linkage to exported MCLK helpers.
