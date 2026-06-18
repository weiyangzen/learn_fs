# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/wcc/Makefile

Purpose: builds the WCC firmware-vendor plugin module for brcmfmac.

Important build objects: it adds include paths for the current directory, parent brcmfmac directory, and shared include directory. It builds `brcmfmac-wcc.o` as an external/module object from `core.o` and `module.o`.

Control flow: build-time only. The compiled module supplies vendor operations registered at module init.

State and persistence: no runtime state in the Makefile. Build outputs are kernel objects/modules controlled by Kbuild.

Dependencies and integration: depends on Kbuild variables and headers under brcmfmac and brcm80211 include paths. It integrates WCC as a separate object rather than folding it into the main brcmfmac module.

Risks and test signals: include path regressions or object list omissions cause module build failures or missing vendor registration. Test with `CONFIG_BRCMFMAC` module builds and ensure `brcmfmac-wcc.ko` exports the expected module metadata and imports namespace `BRCMFMAC` from `module.c`.
