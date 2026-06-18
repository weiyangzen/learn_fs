# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/dcdc.c

Purpose: probes XRX200 DCDC regulator registers and logs core voltage.

Important APIs/functions: `dcdc_probe`, `dcdc_init`, `dcdc_match`, and `dcdc_driver`.

Control flow: `arch_initcall` registers a platform driver for `lantiq,dcdc-xrx200`; probe maps the first resource with devm helpers and reports `DCDC_BIAS_VREG1 * 8` millivolts.

State and persistence: static `dcdc_membase` stores mapped MMIO; no regulator state is modified.

Dependencies and integration: depends on OF platform binding and Lantiq MMIO helpers.

Risks: this is informational only and does not register with the regulator framework. Wrong DT resource prevents logging.

Test signals: DT match, successful resource mapping, and expected voltage line in boot logs.
