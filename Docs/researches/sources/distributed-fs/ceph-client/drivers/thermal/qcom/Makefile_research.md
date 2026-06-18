# sources/distributed-fs/ceph-client/drivers/thermal/qcom/Makefile

Purpose: Kbuild mapping for Qualcomm thermal drivers.

Important entries: `obj-$(CONFIG_QCOM_TSENS) += qcom_tsens.o` and `qcom_tsens-y += tsens.o tsens-v2.o tsens-v1.o tsens-v0_1.o tsens-8960.o` compose the TSENS core plus version backends. Other mappings build `qcom-spmi-adc-tm5.o`, `qcom-spmi-temp-alarm.o`, and `lmh.o` from their matching Kconfig symbols.

Control flow/integration: TSENS version files are not standalone modules; they link into `qcom_tsens`. The SPMI and LMh drivers build as independent objects.

State/persistence: build-time only. Risks/test signals: stale object lists would break compatible data references in the TSENS core; test by building `QCOM_TSENS=m/y` and each independent symbol as module and built-in.
