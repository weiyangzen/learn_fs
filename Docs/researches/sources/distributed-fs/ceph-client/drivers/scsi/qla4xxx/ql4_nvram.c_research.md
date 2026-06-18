<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.c

Purpose: provides low-level EEPROM/NVRAM bit-bang reads and hardware semaphore acquisition for qla4xxx legacy adapters. It validates EEPROM checksums and supplies the locking primitives used by flash/NVRAM/driver/global-resource users.

Important APIs/types/functions: public functions are `rd_nvram_word()`, `rd_nvram_byte()`, `qla4xxx_is_nvram_configuration_valid()`, `ql4xxx_sem_spinlock()`, `ql4xxx_sem_unlock()`, and `ql4xxx_sem_lock()`. Internal helpers are `eeprom_cmd()`, `eeprom_size()`, `eeprom_no_addr_bits()`, `eeprom_no_data_bits()`, `fm93c56a_select()`, `fm93c56a_cmd()`, `fm93c56a_deselect()`, `fm93c56a_datain()`, and `eeprom_readword()`.

Control flow: EEPROM reads select the chip, clock a READ opcode and address one bit at a time through NVRAM register output bits, clock data bits back from input, then deselect the chip. `rd_nvram_word()` reads half-word addressed NVRAM; `rd_nvram_byte()` translates byte offsets to half-word offsets and extracts the correct byte after endian conversion. Checksum validation sums all words for the adapter-specific EEPROM size and accepts only a zero sum. Semaphore lock helpers write mask/code values into the hardware semaphore register and compare the returned owner bits; one variant retries for up to 30 seconds, one is single-shot, and unlock writes the mask to release.

State and persistence: mutates `ha->eeprom_cmd_data` while clocking EEPROM commands. It reads persistent EEPROM content and hardware semaphore ownership but does not write EEPROM data. Semaphore state is shared with firmware/other functions and protects persistent-resource access elsewhere.

Dependencies and integration: depends on MMIO helpers/macros from qla4xxx definitions, adapter-family predicates, `hardware_lock`, and the NVRAM constants/layout in `ql4_nvram.h`/`ql4_fw.h`. Used by initialization to validate NVRAM and configure external hardware.

Risks and test signals: caller locking is mixed: `rd_nvram_word()` says `hardware_lock` must be held, while checksum validation holds it around the whole scan; direct callers must respect that. Bit-banged timing uses `udelay(1)` and fixed address/data widths, so adapter-family detection must be correct. Test signals include checksum success/failure on 4010 vs 4022/4032, byte extraction at odd/even offsets, semaphore contention timeout, unlock after error, and firmware/driver concurrent flash/NVRAM access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.c -->
