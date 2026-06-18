<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ariel-pwrbutton.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/ariel-pwrbutton.c

Purpose: Dell Wyse 3020 "Ariel" EC input driver that reports the EC power button over SPI.

Important APIs/types/functions: `struct ec_input_response` models the five-byte EC response. `ec_input_read()` sends the fixed SPI request. `ec_input_interrupt()` filters duplicate counters, accepts keyboard data message types, translates scan codes `0x74` and `0xf4` to KEY_POWER press/release, and logs unknown codes. `ariel_pwrbutton_probe()` registers input and IRQ.

Control flow and state: probe requires an IRQ, registers a `Power Button` input device, reads the initial message counter, and installs a threaded IRQ. Each IRQ performs one SPI transfer and reports all response bytes up to the encoded size.

State and persistence behavior: only `msg_counter` persists in memory to suppress stale messages. The hardware EC owns scan state.

Dependencies and integration points: depends on SPI, OF compatible `dell,wyse-ariel-ec-input`, SPI device ID `wyse-ariel-ec-input`, threaded IRQs, and Linux input.

Risks: response size/type/counter are trusted after bit extraction. Unknown EC protocol changes are only logged. No explicit locking protects `msg_counter`, relying on threaded IRQ serialization.

Test signals: verify missing IRQ failure, initial counter read, duplicate message suppression, press/release scan codes, unknown message filtering, and SPI transfer errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ariel-pwrbutton.c -->
