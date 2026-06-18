# `sources/distributed-fs/ceph-client/include/linux/iio/afe/rescale.h`

Purpose: IIO analog front-end rescale helper interface for channels whose scale/offset are transformed by resistor dividers, amplifiers, or similar front-end circuitry.

Important APIs/types/functions: `struct rescale_cfg`, `struct rescale`, `rescale_process_scale`, and `rescale_process_offset`.

Control flow and state: `struct rescale` persists source channel, derived channel spec, optional ext-info, processed/raw flag, numerator/denominator gain, and offset. Processing functions transform source scale/offset outputs into rescaled values.

Dependencies/integration: depends on IIO core and IIO consumer channels. Used by AFE rescale drivers and variants selected by `rescale_cfg`.

Risks: rational numerator/denominator and offset arithmetic can overflow or lose precision; `chan_processed` changes interpretation of source data; ext-info allocation/lifetime must match device lifetime.

Test signals: scale/offset conversion vectors for divider/amplifier cases, negative offsets, large numerator/denominator, processed vs raw source channels, and IIO value type propagation.
