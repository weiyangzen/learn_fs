# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/efuse.h

Purpose: Defines shared rtw89 efuse constants, logical-block configuration, and AX/BE efuse parser entry points. It is the common contract between chip bring-up code, AX/BE efuse implementations, and chip-specific efuse interpretation callbacks.

Important APIs, types, and functions: `RTW89_EFUSE_BLOCK_ID_MASK`, `RTW89_EFUSE_BLOCK_SIZE_MASK`, and `RTW89_EFUSE_MAX_BLOCK_SIZE` define the packed block descriptor format used by BE block parsing. `EF_FV_OFSET`, `EF_FV_OFSET_BE_V1`, `EF_CV_MASK`, and `EF_CV_INV` identify efuse version/CV locations and invalid values. `struct rtw89_efuse_block_cfg` stores a packed `offset` and byte `size` for a logical efuse block. Declared functions include AX parsers (`rtw89_parse_efuse_map_ax()`, `rtw89_parse_phycap_map_ax()`, `rtw89_cnv_efuse_state_ax()`), BE parsers (`rtw89_parse_efuse_map_be()`, `rtw89_parse_phycap_map_be()`, `rtw89_cnv_efuse_state_be()`), efuse version readers (`rtw89_read_efuse_ver()`, `rtw89_efuse_read_ecv_be()`), and secure firmware helpers (`rtw89_efuse_recognize_mss_info_v1()`, `rtw89_efuse_read_fw_secure_ax()`, `rtw89_efuse_read_fw_secure_be()`).

Control flow: This header does not implement control flow directly. Consumers choose AX or BE function pointers during chip setup or probe paths, then those implementations dump physical maps, convert them to logical maps, and call chip-specific readers. The block configuration structure is consumed mainly by BE parsing to select HCI/RF/ADIE logical windows out of the packed efuse stream.

State and persistence behavior: The header defines no storage. Its constants determine how implementation files interpret persistent OTP/efuse data into `rtwdev->efuse`, `rtwdev->hal.cv`, phycap data, and `rtwdev->fw.sec`.

Dependencies and integration points: Includes `core.h` for `struct rtw89_dev`, bit macros, and efuse block enum definitions. The declarations are used by chip files that wire operations, by probe paths that parse efuse/phycap data, and by firmware secure-loading code that needs MSS/security metadata.

Risks: The misspelled `EF_FV_OFSET` name is ABI only at source level but should be preserved unless all users are updated. Incorrect block offset packing or size values in chip tables can cause BE parser misreads. Changing `EF_CV_MASK` or invalid value semantics would affect chip version detection and workaround selection.

Test signals: Build coverage should ensure both AX and BE implementation files satisfy these declarations. Runtime validation should compare parsed efuse CV, block sizes, secure-boot fields, and phycap output against known-good devices or golden efuse dumps.
