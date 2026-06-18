# sources/distributed-fs/ceph-client/sound/aoa/codecs/tas-gain-table.h

## Purpose

This header embeds the TAS gain table used to map user-visible half-dB volume and mixer indices to fixed-point hardware gain values.

## Important APIs, types, and functions

The main artifact is `static const int tas_gaintable[]`, with entries from mute/negative infinity through -70.0 dB to +18.0 dB. A commented C/math generator documents the formula used to create the table.

## Control Flow

There is no executable runtime logic except array indexing by `tas.c`. Volume code converts each integer entry into three bytes for TAS volume or mixer registers.

## State and Persistence

The static const table persists in the driver image. It is included exactly once.

## Dependencies and Integration Points

It is included by `tas.c`, which clamps indices to 177 before indexing. It relies on the includer for C type definitions.

## Risks and Test Signals

Risks include index/value mismatch, integer truncation differences from the documented generator, and out-of-range indexing if callers fail validation. Tests should check representative indices, mute, 0 dB, maximum gain, and mixer/volume byte packing.
