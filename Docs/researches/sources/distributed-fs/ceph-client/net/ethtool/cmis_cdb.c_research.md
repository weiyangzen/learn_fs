# sources/distributed-fs/ceph-client/net/ethtool/cmis_cdb.c

## Purpose
This file implements the CMIS CDB transport layer used by ethtool module firmware flashing. It discovers CMIS capabilities, validates optional module passwords, composes and writes CDB commands into module EEPROM pages, polls completion/status/module state fields, copies replies, and reports detailed failure strings.

## Important APIs, Types, And Functions
Public APIs are `ethtool_cmis_get_max_lpl_size()`, `ethtool_cmis_cdb_compose_args()`, `ethtool_cmis_page_init()`, `ethtool_cmis_cdb_check_completion_flag()`, `ethtool_cmis_cdb_init()`, `ethtool_cmis_cdb_fini()`, `ethtool_cmis_wait_for_cond()`, and `ethtool_cmis_cdb_execute_cmd()`. Internal helpers read revision and advertisement bytes, validate password, query module features, poll module bytes, wait for completion/status, process replies, write command pieces, write EPL payload pages, and calculate checksums.

## Control Flow
Initialization allocates `ethtool_cmis_cdb`, reads CMIS revision, rejects revisions below 4, checks CDB advertisement support, optionally writes the password and runs Query Status, then queries module features for max completion time. Command execution computes the checksum over the request fields before EPL, rejects overlong LPL, writes the request body to page `0x9f`, writes EPL data page-by-page if present, writes the command ID last to trigger execution, waits for completion and status according to flags, then reads and validates the reply header/payload when a reply is expected.

## State, Persistence, And Dependencies
Persistent module state changes occur through `set_module_eeprom_by_page()` writes into CMIS command and EPL pages; in-kernel state is limited to the allocated CDB context and command args. Polling uses jiffies, sleeps, and module EEPROM reads. Dependencies include driver `get_module_eeprom_by_page`/`set_module_eeprom_by_page`, netlink extack logging, CMIS constants from `cmis.h`, and module firmware notification helpers.

## Integration Points
`cmis_fw_update.c` builds firmware management commands on top of this transport. `module.c` reaches the firmware update flow, and the device's ethtool ops perform the actual module EEPROM I/O. Error messages are routed to firmware flash notifications and netdev logs.

## Risks
This path writes to optical module management memory, so bad offsets, lengths, checksum coverage, or trigger ordering can brick or confuse modules. Polling must avoid endless waits and must handle vendors that require pre-reply sleeps. Reply validation only checks expected length bounds and nonzero check code, so malformed modules remain a risk. EPL paging loops must stay within `0xa0..0xaf` and offsets `128..255`.

## Test Signals
Tests should simulate CMIS revision rejection, missing advertisement support, password failure, LPL length overflow, EPL multi-page writes, timeout vs status failure messages, reply length/check-code failures, and successful CDB commands with and without replies.
