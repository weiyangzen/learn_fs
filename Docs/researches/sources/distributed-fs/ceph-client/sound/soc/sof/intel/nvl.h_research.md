# sources/distributed-fs/ceph-client/sound/soc/sof/intel/nvl.h

Purpose: declares the Nova Lake ops initializer used by the NVL PCI module.

Important APIs: `sof_nvl_set_ops(struct snd_sof_dev *sdev, struct snd_sof_dsp_ops *dsp_ops)`.

Control flow: no executable code; it lets `pci-nvl.c` call the NVL ops setup while keeping implementation in `nvl.c`.

State and persistence: none.

Dependencies and integration: included by `pci-nvl.c` and `nvl.c`; implementation imports PTL namespace.

Risks and test signals: build coverage is the main signal. Any signature change must be synchronized with `pci-nvl.c`.
