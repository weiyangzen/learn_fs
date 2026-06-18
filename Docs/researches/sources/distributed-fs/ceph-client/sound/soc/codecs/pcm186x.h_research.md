# sources/distributed-fs/ceph-client/sound/soc/codecs/pcm186x.h

Purpose: shared public contract and register map for the PCM186x codec core and its bus drivers. It names device variants, supported PCM rates/formats, virtual paged register addresses, bit fields, and the exported probe/regmap objects.

Important APIs and types: `enum pcm186x_type` differentiates PCM1862 through PCM1865. `PCM186X_RATES` and `PCM186X_FORMATS` advertise 8 kHz to 192 kHz capture and 16/20/24/32-bit sample formats. `extern const struct regmap_config pcm186x_regmap` and `pcm186x_probe(struct device *, enum pcm186x_type, int irq, struct regmap *)` are the core entry points for bus shims.

Control flow contribution: the header encodes paged addressing through `PCM186X_PAGE_LEN`, `PCM186X_PAGE_BASE(n)`, and `PCM186X_PAGE`; the core regmap range config uses these definitions to translate virtual addresses into page-window accesses. Format, TDM, clock, power, status, supply, and memory-map bits are consumed by `pcm186x.c` DAI and power paths.

State and persistence: no runtime state is stored here, but the register definitions govern which fields are cached or volatile in the regmap configuration. `PCM186X_MAX_REGISTER` extends to page 253 current trim control, so a wide virtual register range is exposed.

Dependencies and integration points: depends on Linux PM/regmap declarations and on ALSA PCM bit macros through the including C file context. It is included by the shared core and SPI shim.

Risks: this header exposes many device registers not actively validated by the core, so future controls must respect page addressing and volatile behavior. `PCM186X_RESET` is a value written to the page register, which can be easy to misread as a normal reset register address.

Test signals: compile users of all macros, verify regmap page switching reaches page 0/1/3/253 addresses, and confirm DAI word-length/format bits match the hardware datasheet.
