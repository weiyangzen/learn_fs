# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-avahi-private.h

## Purpose
This private header declares the Avahi TXT record parser used by OSTree repo finder Avahi support.

## Important APIs, Types, And Functions
It includes Avahi and GLib/GIO headers and declares `GHashTable *_ostree_txt_records_parse(AvahiStringList *txt);`.

## Control Flow
There is no runtime control flow in this header. It provides the parser declaration for Avahi finder implementation files and tests.

## State And Persistence
The declaration returns an owned `GHashTable` built by the parser implementation. No state is stored in the header.

## Dependencies And Integration Points
The header depends on `avahi-common/strlst.h`, `gio/gio.h`, `glib-object.h`, and `glib.h`. It integrates `ostree-repo-finder-avahi-parser.c` with the broader Avahi repository discovery implementation.

## Risks And Edge Cases
The main risk is keeping this private declaration synchronized with the parser implementation and ensuring all users understand the returned table's value lifetime constraints from the implementation.

## Test Signals
Build coverage for Avahi-enabled configurations and parser unit tests including this header provide the relevant signal.
