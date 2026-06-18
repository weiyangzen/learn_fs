# sources/distributed-fs/ceph-client/Documentation/networking/device_drivers/atm/cxacru-cf.py

Purpose: this small Python utility converts a Conexant AccessRunner `cxacru-cf.bin` configuration blob from packed little-endian 32-bit words into the text format expected by the driver's sysfs `adsl_config` attribute.

Important APIs, types, and functions: it imports only `sys` and `struct`. The program reads from `sys.stdin` in 4-byte chunks, unpacks each chunk with `struct.unpack("<I", buf)[0]`, and writes `index=value` pairs to stdout with the value formatted in decimal and index in lowercase hexadecimal. Pairs are separated by spaces and terminated by a newline.

Control flow: a loop reads four bytes at a time. End-of-file with zero bytes exits normally. A partial final read writes a newline, emits an error to stderr, and exits with status 1. The index counter starts at zero and increments for every complete word.

State and persistence: there is no persistent state. Runtime state is the current word index and the output stream contents.

Dependencies and integration: integrates with shell pipelines: `cxacru-cf.py < cxacru-cf.bin` produces a string suitable for writing to sysfs. It relies on Python's binary stdin behavior and little-endian word layout documented in the header comments.

Risks: the script uses `sys.stdin.read(4)` without explicitly opening binary stdin; under Python 3 text mode can mishandle arbitrary binary data if invoked as `python3` despite the generic `python` shebang. The file is documentation-era utility code and warns about a known bad MD5/misaligned firmware blob. Test signals include converting a known sequence of little-endian words, partial trailing byte failure, empty input producing only newline, and execution under the intended Python interpreter.
