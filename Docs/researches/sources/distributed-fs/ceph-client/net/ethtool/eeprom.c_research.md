# sources/distributed-fs/ceph-client/net/ethtool/eeprom.c

## Purpose
This file implements ethtool netlink module EEPROM reads, including page/bank-aware module access and a fallback to the older `get_module_info` plus `get_module_eeprom` API.

## Important APIs, Types, And Functions
Important local types are `eeprom_req_info` and `eeprom_reply_data`. Public objects are `ethnl_module_eeprom_request_ops` and `ethnl_module_eeprom_get_policy`. Core helpers include `fallback_set_params()`, `eeprom_fallback()`, `get_module_eeprom_by_page()`, `eeprom_prepare_data()`, `eeprom_parse_request()`, `eeprom_reply_size()`, `eeprom_fill_reply()`, and `eeprom_cleanup_data()`.

## Control Flow
Parsing requires offset, length, page, and I2C address, then enforces half-page and page-boundary constraints; page > 0 may not read the lower half. Preparation allocates a buffer, blocks reads during module firmware flashing, prefers SFP bus page reads, then driver page reads, and falls back to legacy module EEPROM calls on `-EOPNOTSUPP`. Replies contain the data bytes and cleanup frees the allocated buffer.

## State, Persistence, And Dependencies
The operation is read-only against module EEPROM and stores data in a per-reply heap buffer. It depends on `dev->ethtool->module_fw_flash_in_progress`, SFP bus helpers, driver `get_module_eeprom_by_page`, legacy ethtool module EEPROM calls, and netlink extack error reporting.

## Integration Points
The request ops handle `ETHTOOL_MSG_MODULE_EEPROM_GET`. CMIS CDB helpers use the same page-based module EEPROM infrastructure for firmware update operations, while this file provides the userspace read API.

## Risks
Boundary checks are important because module EEPROM pages have low/high halves and page-specific accessibility. Fallback offset translation for SFF-8472 I2C address `0x51` must match legacy ABI. Reads are blocked during firmware flashing to avoid racing management transactions. Reply sizing uses requested length while actual returned length can be shorter, so fill must use `reply->length`.

## Test Signals
Tests should cover required attribute enforcement, offset/length boundary errors, page > 0 lower-half rejection, banked reads, SFP bus path, driver page path, fallback path, firmware-flash `-EBUSY`, short reads, allocation failure, and cleanup on errors.
