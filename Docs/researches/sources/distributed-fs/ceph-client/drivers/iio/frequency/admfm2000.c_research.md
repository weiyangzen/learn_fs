# sources/distributed-fs/ceph-client/drivers/iio/frequency/admfm2000.c

Purpose: platform IIO driver for Analog Devices ADMFM2000 dual microwave downconverter. It controls channel mode routing and digital step attenuator gain through GPIOs.

Important APIs/types/functions: `struct admfm2000_state` stores switch GPIO arrays for two channels, attenuation GPIO arrays for two DSAs, per-channel cached gain, and mutex. `admfm2000_mode()` sets switch GPIO polarity for mixer or direct IF mode. `admfm2000_attenuation()` writes five DSA bits for the selected channel. IIO raw handlers expose `IIO_CHAN_INFO_HARDWAREGAIN`.

Control flow: probe allocates a two-channel IIO direct-mode device, initializes default gain cache, initializes the mutex, and calls `admfm2000_channel_config()`. Channel config iterates firmware child nodes, reads `reg`, chooses mixer/direct mode from `adi,mixer-mode`, obtains switch and attenuation GPIOs by index, and applies mode. Hardware-gain writes convert dB values into a 5-bit inverted attenuation code and update GPIOs under lock.

State/persistence: gain cache is volatile and initialized to `ADMFM2000_DEFAULT_GAIN`; hardware GPIO levels persist only while powered/configured. Mode is applied at probe from firmware and not exposed as runtime IIO state.

Dependencies/integration: platform driver, OF compatible `adi,admfm2000`, firmware child nodes, GPIO descriptor API, and IIO direct mode.

Risks: `mode` is declared bool but assigned enum values; current values are 0/1 so it works. Gain conversion uses bitwise complement and signed arithmetic that deserves tests at boundaries. Channel config does not require both child nodes explicitly. Test signals include firmware children for both channels, missing GPIO errors, mixer/direct switch polarity, gain range -31 dB to 0 dB, and DSA bit ordering.
