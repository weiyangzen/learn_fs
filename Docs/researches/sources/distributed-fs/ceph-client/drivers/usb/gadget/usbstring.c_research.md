<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/usbstring.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/usbstring.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/usbstring.c` provides shared USB gadget helpers for building string descriptors and validating USB language IDs. Gadget drivers use it when answering GET_DESCRIPTOR requests for string descriptor zero and string IDs in a language-specific table. The source was read as a complete 91-line file.

## Important APIs, Types, and Functions

The exported APIs are `usb_gadget_get_string()` and `usb_validate_langid()`. `usb_gadget_get_string()` consumes a `struct usb_gadget_strings` table and a string ID, emits a USB string descriptor into a caller-supplied `u8` buffer, and converts UTF-8 strings to UTF-16LE using `utf8s_to_utf16s()`. `usb_validate_langid()` checks the primary and sublanguage fields in a USB language identifier.

## Control Flow

ID zero is handled specially: the function emits the four-byte language descriptor containing `table->language`. Nonzero IDs are found by linear scan through `table->strings` until a matching `struct usb_string.id` or terminating null string. Missing IDs return `-EINVAL`. Found strings are length-capped to `USB_MAX_STRING_LEN`, converted to UTF-16LE at `buf[2]`, then descriptor length and type are written at bytes zero and one. Language validation rejects reserved primary-language ranges and zero sublanguage values.

## State and Persistence Behavior

The file owns no persistent state. It reads immutable caller-provided string tables and writes only the output descriptor buffer for the current request.

## Dependencies and Integration Points

It depends on kernel NLS conversion helpers, USB Chapter 9 descriptor constants, and `linux/usb/gadget.h` table types. The symbols are exported GPL for gadget drivers and composite functions that implement EP0 string descriptor handling.

## Risks and Edge Cases

The output buffer must be at least 256 bytes and 16-bit aligned as documented; the helper casts `&buf[2]` to `wchar_t *`. Invalid UTF-8 conversion is normalized to `-EINVAL`, which normally stalls the control request. The function trusts `table` and `table->strings` to be valid. `strlen()` plus `USB_MAX_STRING_LEN` caps source bytes, not user-visible characters, before conversion.

## Test Signals

Tests should cover descriptor zero, known and unknown string IDs, maximum-length strings, multi-byte UTF-8 conversion, invalid UTF-8, multiple language tables in gadget setup code, valid common language IDs such as `0x0409`, and rejected primary/sublanguage combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/usbstring.c -->
