# sources/distributed-fs/ceph-client/sound/soc/spear/spear_pcm.h

Purpose: declares the shared SPEAr PCM platform registration helper.

Important APIs/types: `devm_spear_pcm_platform_register()` takes a device, mutable DMAEngine PCM config, and legacy DMA channel filter callback.

Control flow/state: no state; implementation fills the config and registers managed PCM resources.

Dependencies/integration: included by SPEAr S/PDIF drivers that need common PCM setup.

Risks/test signals: users must pass storage for `config` that remains valid for the managed PCM lifetime. Build tests should cover both input and output users.
