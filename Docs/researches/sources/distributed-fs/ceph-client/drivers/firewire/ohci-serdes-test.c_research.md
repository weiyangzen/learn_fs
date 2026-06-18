<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci-serdes-test.c -->
# sources/distributed-fs/ceph-client/drivers/firewire/ohci-serdes-test.c

Purpose: provides KUnit coverage for serialization and deserialization helpers in `ohci.h`, specifically OHCI self-ID count fields, self-ID receive-buffer header fields, asynchronous transmit data quadlets, and isochronous transmit data quadlets.

Important APIs and control flow: `test_self_id_count_register_deserialization()` verifies `ohci1394_self_id_count_is_error()`, generation extraction, and size extraction against a sample `SelfIDCount` value. `test_self_id_receive_buffer_deserialization()` verifies generation and timestamp extraction from the first self-ID receive-buffer quadlet. `test_at_data_serdes()` decodes a three-quadlet OHCI AT DMA header with speed, tlabel, retry, tcode, destination ID, and destination offset, then reserializes it with setter helpers. `test_it_data_serdes()` performs the same round trip for IT DMA speed, tag, channel, tcode, sync, and data length. The suite is registered as `firewire-ohci-serdes`.

State and persistence behavior: no runtime state persists beyond KUnit execution. Test vectors are static constants and local stack buffers.

Dependencies and integration points: depends on KUnit and `ohci.h`. It indirectly validates field helpers used by `ohci.c` while building async transmit descriptors and stream-data descriptors and while parsing self-ID completion state.

Risks and test signals: this test is intentionally narrow and does not exercise MMIO, descriptor DMA, bus resets, or endian quirks beyond little-endian helper use. It can catch mask/shift regressions in `ohci.h`, swapped setter fields, and accidental changes to the expected OHCI DMA header layout. Test signal is a passing KUnit suite named `firewire-ohci-serdes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/ohci-serdes-test.c -->
