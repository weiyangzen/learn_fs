# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cirrus_scodec.h

## Purpose
`cirrus_scodec.h` declares the public helper API for the Cirrus side-codec library.

## APIs, Types, and Functions
The sole declaration is `cirrus_scodec_get_speaker_id(struct device *dev, int amp_index, int num_amps, int fixed_gpio_id)`. It returns a non-negative speaker ID or a negative errno. The header uses include guards and leaves `struct device` as an externally visible kernel type expected from including code.

## Control Flow
There is no control flow in the header. Consumers include it to call the GPIO speaker-ID helper implemented in `cirrus_scodec.c`.

## State and Persistence Behavior
The header defines no state. It documents the call boundary for stateless speaker-ID lookup.

## Dependencies and Integration Points
It integrates `cirrus_scodec.c` with side-codec drivers and KUnit tests. The corresponding implementation exports the function in namespace `SND_HDA_CIRRUS_SCODEC`, so module users must import that namespace.

## Risks
The small surface is low risk, but signature changes would require synchronized updates to tests and every side-codec caller. Since `struct device` is not forward-declared here, consumers must include headers that define it before or indirectly through this header path.

## Test Signals
Compile all consumers, verify namespace imports, and run the Cirrus side-codec KUnit suite to confirm the declared function contract remains stable.
