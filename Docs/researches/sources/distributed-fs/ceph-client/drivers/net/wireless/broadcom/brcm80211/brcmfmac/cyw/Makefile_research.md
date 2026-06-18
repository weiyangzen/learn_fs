# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/cyw/Makefile

Purpose: Builds the Cypress/Infineon brcmfmac firmware-vendor plugin module.

Important APIs/types/functions: Adds include paths for the CYW directory, parent brcmfmac directory, and shared include directory. Defines `obj-m += brcmfmac-cyw.o` and composes it from `core.o module.o`.

Control flow: Kernel/module build uses this file to compile the CYW plugin that registers `brcmf_cyw_ops`.

State and persistence behavior: Build metadata only; no runtime state.

Dependencies and integration points: Include paths allow CYW sources to include parent headers with angle-bracket style. The module depends on BRCMFMAC namespace symbols.

Risks: Include path coupling can hide header collisions. Object naming must match surrounding Kconfig/build integration.

Test signals: `make M=.../brcmfmac/cyw` should produce `brcmfmac-cyw.ko`; modpost should resolve namespace imports.
