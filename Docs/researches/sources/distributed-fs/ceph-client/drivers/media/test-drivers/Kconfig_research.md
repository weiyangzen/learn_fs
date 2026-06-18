# sources/distributed-fs/ceph-client/drivers/media/test-drivers/Kconfig

Purpose: top-level Kconfig menu for virtual V4L and DVB media test drivers. It groups memory-to-memory V4L test devices under `V4L_TEST_DRIVERS` and virtual DVB devices under `DVB_TEST_DRIVERS`.

Important APIs/types/functions: defines `menuconfig V4L_TEST_DRIVERS`, `config VIDEO_VIM2M`, and `menuconfig DVB_TEST_DRIVERS`, and sources child Kconfig files for `vicodec`, `vimc`, `vivid`, `visl`, and `vidtv`.

Control flow: if `V4L_TEST_DRIVERS` is enabled and `VIDEO_DEV` is available, child V4L virtual driver menus become visible. `VIDEO_VIM2M` selects `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, and `MEDIA_CONTROLLER`. If `DVB_TEST_DRIVERS` is enabled and DVB/media/I2C dependencies exist, `vidtv/Kconfig` is sourced.

State and persistence: no runtime state; it controls build-time symbol visibility and dependency propagation.

Dependencies and integration points: depends on media core symbols (`VIDEO_DEV`, `DVB_CORE`, `MEDIA_SUPPORT`, `I2C`) and includes downstream test-driver Kconfig fragments.

Risks: parent menu dependency changes affect many test drivers. `DVB_TEST_DRIVERS` requires I2C because vidtv models tuner/demod attachment through virtual I2C clients.

Test signals: `make menuconfig` visibility checks, `scripts/kconfig/conf` dependency checks, and allmodconfig/randconfig builds with and without `VIDEO_DEV`, `DVB_CORE`, and `I2C`.
