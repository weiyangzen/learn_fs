# sources/distributed-fs/ceph-client/arch/arm/mach-qcom/Kconfig

Purpose: Kconfig entry for ARMv7 Qualcomm devicetree platforms and optional reserved SMEM behavior.

Important APIs/types/functions: `menuconfig ARCH_QCOM` selects GIC, AMBA, Qualcomm clocksource, ARM architected timer, pinctrl, and SCM when SMP is enabled. `ARCH_QCOM_RESERVE_SMEM` reserves 2 MiB at the start of RAM for shared memory.

Control flow: build-time configuration only; enabling `ARCH_QCOM` pulls platform support and allows the SMP code in this directory to build via Makefile.

State and persistence: no runtime state. The SMEM option affects early memory reservation policy elsewhere.

Dependencies and integration points: tied to `ARCH_MULTI_V7`, DT boot, Qualcomm SCM firmware calls, SMP bring-up, and shared-memory expectations for IPQ40xx/MSM8x60/MSM8960.

Risks: selecting SCM only under SMP means non-SMP builds avoid that dependency. Misuse of the SMEM reservation can hide usable RAM or corrupt firmware-owned memory.

Test signals: Kconfig dependency resolution for ARMv7 multi-platform builds and boot tests on Qualcomm DT systems with and without SMEM reservation.
