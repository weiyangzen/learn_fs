# sources/distributed-fs/ceph-client/drivers/iio/test/iio-test-gts.c

Purpose: KUnit suite for IIO gain-time-scale helper logic used by light sensors with gain and integration-time combinations.

Important APIs/types/functions: Defines unsorted test gain/time tables, global `struct iio_gts gts`, and helper `__test_init_iio_gain_scale()`. Tests cover invalid init, `iio_gts_find_gain_sel_for_scale_using_time()`, `iio_gts_find_new_gain_sel_by_old_gain_time()`, `iio_find_closest_gain_low()`, `iio_gts_total_gain_to_scale()`, `iio_gts_avail_times()`, `iio_gts_all_avail_scales()`, and `iio_gts_avail_scales_for_time()`.

Control flow: tests create a KUnit device, initialize GTS tables through devm helper APIs, assert successful and failing lookups, then verify generated available-time and available-scale tables. The suite is registered as `iio-gain-time-scale`.

State and persistence: no persistent state; KUnit devices and devm allocations are test-lifetime resources. The global `gts` is reused but reinitialized per test path.

Dependencies/integration: depends on KUnit device helpers, `linux/iio/iio-gts-helper.h`, and namespace `IIO_GTS_HELPER`. Built by `CONFIG_IIO_GTS_KUNIT_TEST`.

Risks: global `gts` reuse could hide issues if tests ever run concurrently. Expected values encode the helper's sorting and duplicate-time behavior, so helper behavior changes need careful ABI review. Coverage focuses on selected helper branches, not every possible table shape.

Test signals: KUnit suite should pass six cases, including invalid negative/overflow tables and exact available-list contents.
