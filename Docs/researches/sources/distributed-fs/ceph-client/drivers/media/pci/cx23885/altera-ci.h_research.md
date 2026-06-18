# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/altera-ci.h

Exposes Altera CI integration for cx23885 board/DVB code. It defines bus bit masks such as `ALT_DATA`, `ALT_TDI`, `ALT_TDO`, `ALT_TCK`, `ALT_RDY`, `ALT_RD`, `ALT_WR`, `ALT_AD_RG`, and `ALT_CS`.

`struct altera_ci_config` carries main device pointer, DVB adapter, demux, and an `fpga_rw` callback. When `CONFIG_MEDIA_ALTERA_CI` is reachable, real init/release/irq/tuner reset functions are declared; otherwise warning stubs are compiled.

Risks are weak type safety from `void *` fields and silent nonfunctional CI hardware when stubs are active. Test signals are builds with CI built-in, module, and disabled, plus NetUP CI operation.
