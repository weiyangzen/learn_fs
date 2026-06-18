# sources/distributed-fs/ceph-client/include/linux/rational.h

Purpose: declares a helper for finding the best bounded rational approximation to a given fraction, commonly used for clock, PLL, and divider programming.

Important APIs and types: `rational_best_approximation(given_numerator, given_denominator, max_numerator, max_denominator, best_numerator, best_denominator)` computes a numerator/denominator pair within provided limits.

Control flow: drivers call the helper with a target ratio and hardware numerator/denominator maxima, then program registers from the returned approximation.

State and persistence: no state is stored.

Dependencies and integration points: integrates generic continued-fraction style approximation logic with clock/media/display/audio drivers that need constrained ratios.

Risks and test signals: risks include zero denominators, overflow in intermediate products, tie-breaking surprises, and hardware maxima that cannot represent a useful ratio. Test exact ratios, prime/coprime ratios, zero/one limits, large unsigned-long boundaries, and known PLL divider examples.
