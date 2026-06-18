# sources/distributed-fs/lizardfs/src/devtools/mycrc32/mycrc32.cc

Purpose: command-line utility that reads stdin and prints the LizardFS CRC32 of the input.

Important APIs/functions: `main()` allocates a 128 MiB plus one byte buffer, reads stdin with `fread`, rejects inputs filling the buffer, initializes CRC with `mycrc32_init`, computes `mycrc32(0, buffer, bytesRead)`, and prints hex.

Control flow: single pass read into memory, size check, null terminator write after bytes read, CRC calculation, output.

State and persistence: no persistent state; process-local heap buffer and stdout/stderr output.

Dependencies and integration: includes `devtools/mycrc32/mycrc32.h`, `common/crc.h`, Boost scoped array, and `mfscommon`.

Risks: fixed maximum input and full-buffer read make it unsuitable for streaming large files. `fread` byte count is stored in `uint32_t`, safe for the chosen limit but not a general pattern.

Test signals: no direct tests; can be manually compared against known CRC outputs.
