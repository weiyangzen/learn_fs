# `sources/distributed-fs/ceph-client/include/linux/iio/adc-helpers.h`

Purpose: helper API for ADC drivers that describe channels via firmware properties.

Important APIs/types/functions: `iio_adc_device_num_channels` counts named child nodes called `channel`; `devm_iio_adc_device_alloc_chaninfo_se` allocates channel specs from a template with single-ended channel semantics and a max channel ID.

Control flow and state: inline channel count delegates to property/fwnode child counting; allocation is devm-managed and persists until device release.

Dependencies/integration: depends on firmware property APIs and IIO channel specs. Used by ADC drivers parsing DT/ACPI child channels.

Risks: only children named exactly `channel` are counted; channel IDs must be bounded by `max_chan_id`; template fields must be safe to clone.

Test signals: firmware nodes with zero/one/multiple channel children, invalid channel IDs, devm cleanup on probe failure, and generated channel spec contents.
