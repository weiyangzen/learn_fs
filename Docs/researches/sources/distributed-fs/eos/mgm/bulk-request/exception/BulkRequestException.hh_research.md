## sources/distributed-fs/eos/mgm/bulk-request/exception/BulkRequestException.hh

Purpose: declares a simple `std::exception` subclass carrying a bulk-request error message.

Important API/state: constructor from string stores `mErrorMsg`; `what()` returns `mErrorMsg.c_str()`.

Integration: included by `BulkRequestPrepareManager.cc`, though the read code does not actively throw it there. Risks include class being outside the EOS bulk namespace, unlike most bulk-request code, and `what()` lacking `override` in style. Tests are minimal: construct and assert `what()` stability.
